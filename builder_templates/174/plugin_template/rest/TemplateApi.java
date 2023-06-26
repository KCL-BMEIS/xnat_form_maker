/*
 * xnat-template: org.nrg.xnat.plugins.template.rest.TemplateApi
 * XNAT http://www.xnat.org
 * Copyright (c) 2017, Washington University School of Medicine
 * All Rights Reserved
 *
 * Released under the Simplified BSD.
 */

package org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].rest;

import io.swagger.annotations.Api;
import io.swagger.annotations.ApiOperation;
import io.swagger.annotations.ApiResponse;
import io.swagger.annotations.ApiResponses;
import org.nrg.framework.annotations.XapiRestController;
import org.nrg.xapi.rest.AbstractXapiRestController;
import org.nrg.xapi.rest.XapiRequestMapping;
import org.nrg.xdat.security.services.RoleHolder;
import org.nrg.xdat.security.services.UserManagementServiceI;
import org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].entities.[HERE_SCHEMANAME];
import org.nrg.xnat.plugins.[HERE_SCHEMANAME_LOWER].services.[HERE_SCHEMANAME]Service;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

import java.util.List;

@Api(description = "XNAT 1.7 [HERE_SCHEMANAME] Plugin API")
@XapiRestController
@RequestMapping(value = "/[HERE_SCHEMANAME_LOWER]/entities")
public class [HERE_SCHEMANAME]Api extends AbstractXapiRestController {
    @Autowired
    protected [HERE_SCHEMANAME]Api(final UserManagementServiceI userManagementService, final RoleHolder roleHolder, final [HERE_SCHEMANAME]Service templateService) {
        super(userManagementService, roleHolder);
        _templateService = templateService;
    }

    @ApiOperation(value = "Returns a list of all templates.", response = [HERE_SCHEMANAME].class, responseContainer = "List")
    @ApiResponses({@ApiResponse(code = 200, message = "[HERE_SCHEMANAME]s successfully retrieved."),
                   @ApiResponse(code = 401, message = "Must be authenticated to access the XNAT REST API."),
                   @ApiResponse(code = 500, message = "Unexpected error")})
    @XapiRequestMapping(produces = {MediaType.APPLICATION_JSON_VALUE}, method = RequestMethod.GET)
    public ResponseEntity<List<[HERE_SCHEMANAME]>> getEntities() {
        return new ResponseEntity<>(_templateService.getAll(), HttpStatus.OK);
    }

    @ApiOperation(value = "Creates a new template.", response = [HERE_SCHEMANAME].class)
    @ApiResponses({@ApiResponse(code = 200, message = "[HERE_SCHEMANAME] successfully created."),
                   @ApiResponse(code = 401, message = "Must be authenticated to access the XNAT REST API."),
                   @ApiResponse(code = 500, message = "Unexpected error")})
    @XapiRequestMapping(produces = {MediaType.APPLICATION_JSON_VALUE}, method = RequestMethod.POST)
    public ResponseEntity<[HERE_SCHEMANAME]> createEntity(@RequestBody final [HERE_SCHEMANAME] entity) {
        final [HERE_SCHEMANAME] created = _templateService.create(entity);
        return new ResponseEntity<>(created, HttpStatus.OK);
    }

    @ApiOperation(value = "Retrieves the indicated template.",
                  notes = "Based on the template ID, not the primary key ID.",
                  response = [HERE_SCHEMANAME].class)
    @ApiResponses({@ApiResponse(code = 200, message = "[HERE_SCHEMANAME] successfully retrieved."),
                   @ApiResponse(code = 401, message = "Must be authenticated to access the XNAT REST API."),
                   @ApiResponse(code = 500, message = "Unexpected error")})
    @XapiRequestMapping(value = "{id}", produces = {MediaType.APPLICATION_JSON_VALUE}, method = RequestMethod.GET)
    public ResponseEntity<[HERE_SCHEMANAME]> getEntity(@PathVariable final String id) {
        return new ResponseEntity<>(_templateService.findByTemplateId(id), HttpStatus.OK);
    }

    @ApiOperation(value = "Updates the indicated template.",
                  notes = "Based on primary key ID, not subject or record ID.",
                  response = Void.class)
    @ApiResponses({@ApiResponse(code = 200, message = "[HERE_SCHEMANAME] successfully updated."),
                   @ApiResponse(code = 401, message = "Must be authenticated to access the XNAT REST API."),
                   @ApiResponse(code = 500, message = "Unexpected error")})
    @XapiRequestMapping(value = "{id}", produces = {MediaType.APPLICATION_JSON_VALUE}, method = RequestMethod.PUT)
    public ResponseEntity<Void> updateEntity(@PathVariable final Long id, @RequestBody final [HERE_SCHEMANAME] entity) {
        final [HERE_SCHEMANAME] existing = _templateService.retrieve(id);
        existing.setTemplateId(entity.getTemplateId());
        _templateService.update(existing);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    @ApiOperation(value = "Deletes the indicated template.",
                  notes = "Based on primary key ID, not subject or record ID.",
                  response = Void.class)
    @ApiResponses({@ApiResponse(code = 200, message = "[HERE_SCHEMANAME] successfully deleted."),
                   @ApiResponse(code = 401, message = "Must be authenticated to access the XNAT REST API."),
                   @ApiResponse(code = 500, message = "Unexpected error")})
    @XapiRequestMapping(value = "{id}", produces = {MediaType.APPLICATION_JSON_VALUE}, method = RequestMethod.DELETE)
    public ResponseEntity<Void> deleteEntity(@PathVariable final Long id) {
        final [HERE_SCHEMANAME] existing = _templateService.retrieve(id);
        _templateService.delete(existing);
        return new ResponseEntity<>(HttpStatus.OK);
    }

    private final [HERE_SCHEMANAME]Service         _templateService;
}
